import { Box, Heading, Text, Button, HStack } from '@chakra-ui/react'

export default function CityQuiz({ target, score, attempts, streak, result, onReset }) {
  return (
    <Box py={4}>
      {target ? (
        <Heading size="md">Find: {target}</Heading>
      ) : (
        <Heading size="md" color="gray.500">Loading…</Heading>
      )}

      <HStack spacing={6} mt={2}>
        <Text>Score: {score} / {attempts}</Text>
        <Text>Streak: {streak}</Text>
      </HStack>

      {result && (
        <Text mt={2} fontWeight="bold" color={result.correct ? 'green.500' : 'red.500'}>
          {result.correct ? 'Correct!' : 'Not quite — the highlighted area is correct.'}
        </Text>
      )}

      <Button mt={3} size="sm" onClick={onReset}>Reset</Button>
    </Box>
  )
}
